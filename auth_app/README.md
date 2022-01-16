# Auth service

This service is intended to be used as an entrypoint for all microservices like: **ETL** or **Async_api**

## How to run

In order to launch the application simply enter the next docker command:
`docker-compose up -d --build`

After that you can make a server health-check via **curl**:
```
curl --location --request GET 'http://localhost/api/v1/smoke'
```
In order to see swagger-docs, use **this endpoint**:
```
http://localhost/api/v1/apidocs/
```