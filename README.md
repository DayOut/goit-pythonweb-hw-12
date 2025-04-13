To init project you need:
- start containers
  - in separate window `docker-compose up --build`
  - or with `-d` option `docker-compose up --build -d` to close later manually
- go to app cli
  - `docker-compose exec app sh`
  - then inside container run migrations with `alembic upgrade head`

Then you can go to [localhost:8000](http://localhost:8000/docs) to open OpenAPI page.

For any further launches you need only start containers with `docker-compose up --build` or `docker-compose up --build -d` 