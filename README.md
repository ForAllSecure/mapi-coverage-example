# Mayhem for API: REST API example with Non-Trival Issue

[![Mayhem for API](https://mayhem4api.forallsecure.com/downloads/img/mapi-logo-full-color.svg)](http://mayhem4api.forallsecure.com/signup)

## About Mayhem for API

🧪 Modern App Testing: Mayhem for API is a dynamic testing tool that
catches reliability, performance and security bugs before they hit
production.

🧑‍💻 For Developers, by developers: The engineers building
software are the best equipped to fix bugs, including security bugs. As
engineers ourselves, we're building tools that we wish existed to make
our job easier!

🤖 Simple to Automate in CI: Tests belong in CI, running on every commit
and PRs. We make it easy, and provide results right in your PRs where
you want them. Adding Mayhem for API to a DevOps pipeline is easy.

Want to try it? [Sign up for free](http://mayhem4api.forallsecure.com/signup)!

## Example REST API

This repo contains a simple python API that contains a SQL Injection which
requires a specific sequence of API calls for it to be triggered.

### Start the API

Docker Compose is the easiest way to get the API up and running:

```bash
docker compose up
```

# Scan with Mayhem for API

You will need to [sign up](https://mayhem4api.forallsecure.com/signup) and
download the Mayhem for API CLI, `mapi` to continue:

```bash
mapi run coverage-demo \
30sec \
http://localhost:8000/openapi.json \
--url http://localhost:8000 \
--html report.html
```

When your run completes, you can check the results in the `report.html` file
created by `mapi` or on your [target dashboard](https://mayhem4api.forallsecure.com).