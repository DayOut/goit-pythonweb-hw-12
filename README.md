To init project you need:
- create your `.env` file
  - copy example file and remove `.example` part
  - fill all fields 
- start containers
  - in separate window `docker-compose up --build`
  - or with `-d` option `docker-compose up --build -d` to close later manually
- go to app cli
  - `docker-compose exec app sh`
- inside container run migrations with `alembic upgrade head`
- You are breathtaking 🎉 

Then you can go to [localhost:8000](http://localhost:8000/docs) to open OpenAPI page.
There you can see all logic for this app.

For any further launches you need only start containers with `docker-compose up --build` or `docker-compose up --build -d` 