# **project-http — Rebuilding the Web From Scratch**

A minimal educational project that rebuilds the early Web exactly the way Tim Berners-Lee designed it:
**raw TCP sockets → HTTP → URL parsing → routing → dynamic content.**
No frameworks, no magic — just the real mechanics of how browsers and servers communicate.

---

## **What this project does**

You will learn how to:

* Open a TCP socket and serve HTTP responses manually.
* Parse raw HTTP requests (`GET / HTTP/1.1`, headers, body).
* Implement simple routing (`/`, `/hello`, 404).
* Parse URLs into `path` + `query string`.
* Generate dynamic pages (e.g., `/hello?name=Minh`).
* Run a small server that handles multiple requests sequentially.

This reproduces the core behaviour of early HTTP/0.9 → 1.0 → 1.1 servers.

---

## **Project Structure**

```
project-http/
│
├── src/
│   └── simple_http_server.py
└── README.md
```

---

## **Main Learning Steps**

1. **Minimal HTTP Server**
   Create a tiny web server using raw `socket` (no frameworks).

2. **HTTP Request Parsing**
   Convert raw bytes into `method`, `path`, `version`, `headers`, `body`.

3. **Basic Routing**
   Serve different HTML pages for `/`, `/hello`, and return 404 for unknown paths.

4. **Multiple Requests**
   Use a loop around `accept()` to keep the server running (HTTP/1.0 style).

5. **URL Query Parameters**
   Split `/hello?name=Minh` into path + query dict and generate dynamic HTML.

---

## **How to run**

```bash
python -m src.simple_http_server
```

Then open in a browser:

* [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
* [http://127.0.0.1:8080/hello](http://127.0.0.1:8080/hello)
* [http://127.0.0.1:8080/hello?name=Minh](http://127.0.0.1:8080/hello?name=Alice)

Stop the server with **Ctrl + C**.

---

## **Future Extensions**

* Keep-alive connections (HTTP/1.1 behaviour)
* Static file serving
* JSON API endpoints
* URL decoding (`%20`, `+`)
* Multi-threaded / async server