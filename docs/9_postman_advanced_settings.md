# Postman Advanced Settings

From the Postman app we can configure collections, environment variables, authorization, and scripts to automate
repetitive tasks such as storing the JWT token after every login.

1. [Create a collection](#1-create-a-collection)
2. [Create environment variables](#2-create-environment-variables)
3. [Automate JWT token storage with a script](#3-automate-jwt-token-storage-with-a-script)
4. [Set authorization at the collection level](#4-set-authorization-at-the-collection-level)

## 1. Create a collection

- Open the **left sidebar**
- Click the **`+`** icon next to the search bar and select **Collection**
- Rename the collection — for example: `FastAPI`
- Inside the collection, group requests by resource

**Example:**

```text
FastAPI
├── auth
│   └── POST  /login                     (public)
├── users
│   ├── POST  /users                     (public — create user)
│   └── GET   /users/{id}               (public — get user by id)
└── posts
    ├── GET   /posts                     (JWT required)
    ├── GET   /posts/latest              (JWT required)
    ├── GET   /posts/{id}               (JWT required)
    ├── POST  /posts                     (JWT required — create post)
    ├── PUT   /posts/{id}               (JWT required — update post)
    └── DELETE /posts/{id}              (JWT required — delete post)
```

> **Important:** Every `/posts` route is JWT-protected — including all read operations. Only `POST /login` and
> the `/users` endpoints are public. Requests to `/posts` without a valid Bearer token return `401 Unauthorized`.

## 2. Create environment variables

Environments let you manage sets of variables so you can switch context (e.g. `DEV` vs `PROD`) without editing
individual requests.

- Open the **left sidebar**
- Click the **`+`** icon and select **Environment**
- Name it — for example: `DEV:FastAPI`
- Add the following variables:

| Variable   | Type    | Initial Value           | Notes                             |
|------------|---------|-------------------------|-----------------------------------|
| `BASE_URL` | default | `http://127.0.0.1:8000` | Base URL for all requests         |
| `JWT`      | secret  | *(leave empty)*         | Populated automatically by script |

Use environment variables in request URLs:

```text
{{BASE_URL}}/posts/
```

- Select the active environment from the **Environment** dropdown (top-right of Postman)

## 3. Automate JWT token storage with a script

After a successful login, the API returns an `access_token`. We can write a post-response script on the login
request to store this token automatically in `{{JWT}}`.

- Select the **`POST /login`** request
- Open the **Scripts** tab
- Under **Post-response**, add the following script:

```javascript
pm.environment.set("JWT", pm.response.json().access_token);
```

> **Note:** `access_token` is the key in the `/login` response body (defined in `schemas.Token`). The token
> expires after **60 minutes** (`ACCESS_TOKEN_EXPIRE_MINUTES = 60` in `app/oauth2.py`). After expiry, re-run
> the login request and the script will refresh `{{JWT}}` automatically.

Once configured:

1. Run **`POST /login`** with valid credentials
2. The script stores the returned token in `{{JWT}}`
3. All other requests that reference `{{JWT}}` will use the latest token

## 4. Set authorization at the collection level

Instead of adding a Bearer Token to every individual request, configure it **once on the collection** and let all
child requests inherit it automatically.

- Right-click the **FastAPI** collection and select **Edit**
- Open the **Authorization** tab
- Set **Auth Type** to `Bearer Token`
- In the **Token** field enter `{{JWT}}`
- Click **Save**

Now in each individual request, set **Authorization** → **Auth Type** to `Inherit auth from parent`. The
collection-level Bearer Token is applied automatically.

**Key points:**

- `POST /login` and `POST /users` should have **Auth Type** set to `No Auth` (they are public endpoints)
- All `/posts` requests should use `Inherit auth from parent`
- When `{{JWT}}` is updated by the login script, every inherited request picks up the new token immediately
