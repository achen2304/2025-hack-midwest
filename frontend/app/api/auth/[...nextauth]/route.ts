import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import bcrypt from 'bcryptjs';
import clientPromise from '@/lib/mongo/client';

export const authOptions = {
  providers: [
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

const handler = NextAuth(authOptions as any);
export { handler as GET, handler as POST };
