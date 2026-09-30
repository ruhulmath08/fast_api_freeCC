# Postman advanced settings

From the postman app, we can configure the settings of the app like environment variables, URL, headers, body,
parameters, bearer token etc.

1. Create collection
2. Create Environment variables
3. Write a script to create a JWT token and store it in the environment variables.

## 1. Create collection

- Open the `left sidebar`
- From the top section right side of the search bar click the `+` icon and click `Collection`
- Now rename the collection name and give a name to the collection. For example: `FastAPI`
- Inside the collection we can group the requests by name of the API. For example: `Users`, `Posts`, `Comments`

**Example:**

```text
FastAPI
  - auth
    - POST login
    - POST register
  - users
    - POST createUser
    - GET getUserById
    - PUT updateUserById
    - DELETE deleteUserById
  - posts
    - GET AllPosts
    - GET GetPostById
    - GET GetLatestPost
    - POST CreatePost
    - PUT UpdatePost
    - DELETE DeletePost
```

## 2. Environment variables

Environments allow you to manage sets of variables that let you switch the context of your requests easily. You can
create a new environment by follow the following steps

- Open the `left sidebar`
- From the top section right side of the search bar click the `+` icon and click `Environment`
- Rename the name of the environment. Example: `DEV:FastAPI`
- Now select the environment variables that you want to use in the requests. For example: `BASE_URL`, `JWT` etc.
- Now you can use the environment variables in the requests. For example: `{{BASE_URL}}`, `{{JWT}}` etc.
- Now you can switch the environment by clicking the `Environment` dropdown and selecting the environment.

**Example:**

| Variable   | Value                                                                                                                         |
|------------|-------------------------------------------------------------------------------------------------------------------------------|
| `BASE_URL` | `http://127.0.0.1:8000`                                                                                                       |
| `JWT`      | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxOSwiZXhwIjoxNzkwNzkyMTcwfQ.49khce5Gdt5FjL8bWl-qx-ZcSHdg2ffWZv7wDyElZ0Q` |

Use the environment variables in the requests. For example: `{{BASE_URL}}`, `{{JWT}}` etc.

```text
{{BASE_URL}}/posts/
```

## 3. Write a script to create a JWT token and store it in the environment variables

Now we will write a script to create a JWT token and store it in the environment variables automatically after the login
request is successful.

- Select the `login` request
- Select the `Script` tab
- Select the `After Response` tab
- Write the following script:

```javascript
pm.environment.set("JWT", pm.response.json().access_token);
```

> Note: Here `access_token` is the key of the response body. You can get the key of the response body by clicking the
> `Response` tab and then clicking the `Body` tab.

- Now after the login request is successful, the JWT token will be created and stored in the environment variables and
  assign the value to the `JWT` environment variable.
- Now you can use the JWT token in the requests. For example: `{{JWT}}` etc.
- Now from authorization header, select the `Bearer Token` option and paste the `{{JWT}}` environment variable in the
  token field.
