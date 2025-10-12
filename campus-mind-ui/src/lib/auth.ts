import CredentialsProvider from 'next-auth/providers/credentials';
import bcrypt from 'bcryptjs';
import clientPromise from '@/lib/mongo/client';
import Google from 'next-auth/providers/google';
import { NextAuthOptions } from 'next-auth';

export const authOptions: NextAuthOptions = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      // Default scopes include openid email profile; fine as-is
    }),

    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        const client = await clientPromise;
        const db = client.db(process.env.DB_NAME || 'campusmind'); // Use same DB as backend
        // Only pull what you need
        const user = await db
          .collection('users')
          .findOne(
            { email: credentials.email },
            {
              projection: {
                _id: 1,
                email: 1,
                name: 1,
                image: 1,
                hashedPassword: 1,
              },
            }
          );

        if (!user?.hashedPassword) return null;

        const ok = await bcrypt.compare(
          credentials.password,
          user.hashedPassword
        );
        if (!ok) return null;

        return {
          id: user._id.toString(),
          email: user.email,
          name: user.name ?? null,
          image: user.image ?? null,
        };
      },
    }),
  ],
  session: { strategy: 'jwt' },
  secret: process.env.NEXTAUTH_SECRET,
  callbacks: {
        /** Ensure there is a Mongo user for Google sign-ins; link by email */
    async signIn({ user, account }) {
      if (account?.provider !== 'google') return true;
      if (!user?.email) return false;
      const client = await clientPromise;
      const db = client.db(process.env.DB_NAME || 'campusmind');
      const existing = await db.collection('users').findOne({ email: user.email });

      if (!existing) {
        // Create a new user record for this Google account
        const { insertedId } = await db.collection('users').insertOne({
          email: user.email,
          name: user.name ?? null,
          image: user.image ?? null,
          // no hashedPassword for OAuth users
          createdAt: new Date(),
          provider: 'google',
        });
        // attach the new _id for jwt callback via a temporary property
        (user as any)._mongoId = insertedId.toString();
      } else {
        // Optionally keep profile fresh
        await db.collection('users').updateOne(
          { _id: existing._id },
          { $set: { name: existing.name ?? user.name ?? null, image: user.image ?? existing.image ?? null } }
        );
        (user as any)._mongoId = existing._id.toString();
      }
      return true;
    },

    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id; // useful: put id on token
        token.email = user.email;
        token.name = user.name ?? null;
        token.picture = user.image ?? null;
      }
      return token;
    },
    async session({ session, token }) {
      if (!session.user) session.user = {};
      session.user.id = token.sub;
      session.user.email = token.email;
      session.user.name = token.name ?? null;
      session.user.image = token.picture ?? null;
      return session;
    },
  },
};