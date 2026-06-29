# Deployment on linux based server

## Configuration (RAILWAY)

rootDir = <repo-root>/<project>

### See [Environment variables](.env.railway)

### See [Dependencies](boilerplate/requirements.txt)

buildCommand = "python manage.py collectstatic --noinput"
Collect all static file from different directories like <project-name>/<app-name>/static or Folders defined under STATICFILES_DIR and store them /<STATIC_ROOT> and /<STATIC_URL> as href.

preDeployCommand = "python manage.py migrate"
executes migration (in DB) instructions under /<app-name>/migrations which can be automade by python manage.py makemigrate <app-name>

startCommand = "gunicorn boilerplate.wsgi:application --bind 0.0.0.0:$PORT"
run the WSGI (an interface/ adapter between web server (gunicorn) and framework(django)) HTTP server loading /<project-name>/wsgi.py which executes the django framework services, listening on 0.0.0.0:$PORT , 0.0.0.0 = all addresses on local machine at $PORT

healthcheckPath = "${{baseURL}}/api/"
expects a 200 ok response, no redirects!

## Execution

                     Browser
                        │
                  HTTPS Request
                        │
                DNS Resolution
                        │
                        ▼
              Public IP of Server
                        │
                  Linux Firewall
                        │
                        ▼
                     Nginx
                        │
             (Reverse Proxy)
                        │
                        ▼
                  Gunicorn
                        │
                WSGI Interface
                        │
                        ▼
                 Django Project
          ┌──────────┴──────────┐
          ▼                     ▼
      MySQL                 Redis
          │
          ▼
       Storage

Nginx (Reverse Proxy) or Railway Edge Proxy is front-facing server, intercepts and forward request to appropriate back server and collecting responses, handling traffic. Single Threaded
Security features:
    hiding actual IP addresses of server running the business.
    Load Balancing
    blocks malicious requests
    SSL Termination (Decrypts incoming secure requests and encrypts outgoing responses)
    Caching (stores static content, make faster, delegate the work from back)

Gunicorn the back server dealing with business content (our logic written in python is executed), building client response, interacting with caches, DB and other APIs. Multi Threaded (Worker Pool)

## DJANGO settings failing health checks

### HSTS

SECURE_HSTS_SECONDS
SECURE_HSTS_INCLUDE_SUBDOMAINS
SECURE_HSTS_PRELOAD

if preload is on or duration is too long, your browser itself does not allow you to access via http.

### SSL

SECURE_SSL_REDIRECT
SECURE_PROXY_SSL_HEADER
CSRF_COOKIE_SECURE
SESSION_COOKIE_SECURE

SSL is terminated before request is received (http) by django by reverse proxy, django deem the request to be insecure (request.is_secure() == False) . Then **SECURE_SSL_REDIRECT = True causes an infinite redirect**, never reply with a response:
HTTPS Client -> Railway Proxy -> Django thinks:"I'm on HTTP" -> Redirect to HTTPS -> Client is already on HTTPS -> Repeat forever

**FIX: SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") OR TURN OFF SSL VALIDATION**
This tells Django: "If the proxy says the original request was HTTPS, treat it as HTTPS."

### white lists

ALLOWED_HOSTS -> checks desired destination (HOST HEADER)
The Threat: Attackers can send a request to your server's IP address but manipulate the HTTP Host header to say evil-attacker.com. If Django uses that header to generate absolute links (like password reset emails), your site will accidentally send users to the attacker's site.

CSRF_TRUSTED_ORIGINS -> origin of request, which domain created the request (ORIGIN HEADER)
The Threat: A user is logged into your banking app (example.com). They visit a malicious site (evil.com) in another tab. evil.com executes a hidden background script that submits a form to your bank app. Since the user is logged in, their browser automatically sends their session cookie, and the bank processes the transaction.

Only the request has host header which are white listed, **not necessary that same as request destination**, are processed.

if Frontend and backend on different domains, You must also configure Django CSRF_TRUSTED_ORIGINS, SESSION_COOKIE_SAMESITE, and **CORS with credentials** for cross-origin session auth.

## RAILWAY SKILL-ISSUE

Once the root directory is changes, Railway cannot access files in parent directory which exist in repository. Cannot collect static files. Since no manage.py before "cd <specified-root>" python or pip is not installed.
FIX: move the files inside

Use shared variables
