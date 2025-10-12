# Security Guide for CampusMind

This document outlines the security measures implemented in CampusMind to protect sensitive information and private keys.

## 🔒 Protected Information

The `.gitignore` file has been configured to protect the following types of sensitive information:

### Environment Variables & Secrets
- `.env` files containing API keys, database URLs, and configuration
- Environment-specific files (`.env.local`, `.env.production`, etc.)
- Example: `MONGODB_URI`, `CANVAS_TOKEN`, `NEXTAUTH_SECRET`

### API Keys & Tokens
- Canvas LMS API tokens
- JWT secrets and session keys
- Third-party service API keys
- OAuth client secrets
- Social media API keys

### Database Credentials
- MongoDB connection strings
- Database configuration files
- Connection credentials

### SSL/TLS Certificates
- Private keys (`.key`, `.pem`)
- Certificates (`.crt`, `.cer`)
- Certificate signing requests (`.csr`)
- Key stores (`.jks`, `.p12`, `.pfx`)

### Cloud Provider Credentials
- AWS credentials and configuration
- Azure service principal keys
- Google Cloud Platform credentials
- Firebase service account keys

### Payment & Financial Data
- Stripe secret keys
- PayPal API credentials
- Payment processing configurations

## 🛡️ Security Best Practices

### 1. Environment Variables
Always use environment variables for sensitive configuration:

```bash
# Backend (.env)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
CANVAS_TOKEN=your_canvas_token_here
JWT_SECRET=your_jwt_secret_here
NEXTAUTH_SECRET=your_nextauth_secret_here

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
```

### 2. Canvas API Integration
For Canvas LMS integration:

1. **Generate Canvas Token**:
   - Go to Canvas → Account → Settings → Approved Integrations
   - Create new access token with minimal required permissions

2. **Required Permissions**:
   - `url:GET|/api/v1/courses` - Read courses
   - `url:GET|/api/v1/courses/:course_id/assignments` - Read assignments
   - `url:GET|/api/v1/calendar_events` - Read calendar events
   - `url:GET|/api/v1/users/self` - Read user profile

3. **Store Securely**:
   ```bash
   # Never commit to git
   CANVAS_TOKEN=1234~your_actual_token_here
   CANVAS_BASE_URL=https://your-university.instructure.com
   ```

### 3. Database Security
For MongoDB Atlas:

1. **Use Connection String with Credentials**:
   ```bash
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
   ```

2. **Enable Network Access Restrictions**:
   - Whitelist specific IP addresses
   - Use MongoDB Atlas IP whitelist

3. **Use Database Users**:
   - Create specific database users with minimal permissions
   - Avoid using admin accounts in applications

### 4. Authentication Security
For NextAuth.js:

1. **Generate Strong Secrets**:
   ```bash
   # Generate random secret
   openssl rand -base64 32
   
   # Use in environment
   NEXTAUTH_SECRET=your_generated_secret_here
   ```

2. **Secure Session Configuration**:
   ```javascript
   // Use secure cookies in production
   cookies: {
     sessionToken: {
       name: `__Secure-next-auth.session-token`,
       options: {
         httpOnly: true,
         sameSite: 'lax',
         path: '/',
         secure: process.env.NODE_ENV === 'production'
       }
     }
   }
   ```

## 🔍 Security Checklist

### Before Committing Code
- [ ] No hardcoded API keys or secrets
- [ ] All sensitive data in environment variables
- [ ] No database credentials in code
- [ ] No Canvas tokens in code
- [ ] No JWT secrets in code
- [ ] No SSL certificates in repository
- [ ] No cloud provider credentials
- [ ] No payment processing keys

### Environment Setup
- [ ] Create `.env` files from `.env.example`
- [ ] Set strong, unique passwords
- [ ] Use HTTPS in production
- [ ] Enable CORS properly
- [ ] Set secure cookie options
- [ ] Use environment-specific configurations

### Canvas Integration
- [ ] Canvas token has minimal permissions
- [ ] Canvas URL is correct for your institution
- [ ] Token is stored in environment variables
- [ ] Test connection before deployment

### Database Security
- [ ] MongoDB Atlas cluster is secured
- [ ] Network access is restricted
- [ ] Database users have minimal permissions
- [ ] Connection string uses environment variables

## 🚨 Security Alerts

### If You Accidentally Commit Secrets

1. **Immediately Rotate Credentials**:
   - Generate new API keys
   - Update database passwords
   - Revoke old tokens

2. **Remove from Git History**:
   ```bash
   # Remove file from git history
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch path/to/secret/file' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Force push to remote
   git push origin --force --all
   ```

3. **Update .gitignore**:
   - Add patterns to prevent future commits
   - Test with `git check-ignore` command

## 📝 Security Documentation

### Canvas API Security
- [Canvas API Authentication](https://canvas.instructure.com/doc/api/file.oauth.html)
- [Canvas API Permissions](https://canvas.instructure.com/doc/api/permissions.html)
- [Canvas API Rate Limiting](https://canvas.instructure.com/doc/api/file.rate_limiting.html)

### MongoDB Security
- [MongoDB Atlas Security](https://docs.atlas.mongodb.com/security/)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/security-checklist/)

### NextAuth.js Security
- [NextAuth.js Security](https://next-auth.js.org/configuration/options#security-options)
- [NextAuth.js Deployment](https://next-auth.js.org/deployment)

## 🔧 Security Tools

### Environment Variable Validation
Create a validation script to ensure all required environment variables are set:

```javascript
// scripts/validate-env.js
const requiredEnvVars = [
  'MONGODB_URI',
  'NEXTAUTH_SECRET',
  'CANVAS_TOKEN',
  'CANVAS_BASE_URL'
];

const missing = requiredEnvVars.filter(envVar => !process.env[envVar]);

if (missing.length > 0) {
  console.error('Missing required environment variables:', missing);
  process.exit(1);
}

console.log('✅ All required environment variables are set');
```

### Secret Scanning
Use tools to scan for accidentally committed secrets:

```bash
# Install truffleHog for secret scanning
pip install truffleHog

# Scan repository for secrets
truffleHog --regex --entropy=False file://.
```

## 📞 Security Contacts

If you discover a security vulnerability:

1. **Do not** create a public issue
2. **Do not** commit fixes to public repository
3. Contact the development team privately
4. Provide detailed information about the vulnerability

## 🔄 Regular Security Updates

- Review and rotate API keys quarterly
- Update dependencies regularly
- Monitor security advisories
- Conduct security audits
- Update SSL certificates before expiration

---

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures to protect your application and users' data.
