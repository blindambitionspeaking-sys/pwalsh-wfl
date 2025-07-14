![Banner](./wind_for_life/static/images/png/wind4life_banner.png)
# Table of Contents
1. [Introduction](#introduction)
2. [List of features to implement](#list-of-features-to-implement)
3. [Getting started](#getting-started)

# Introduction

Fieldbox's technical test

FieldBox.ai just got selected in the final round for a new business opportunity: refactoring the
backend for the application of WindForLife, a non-profit organization providing real-time wind
data around the world.

# List of features to implement

- Users are able to manage anemometers (CRUD).
- Users are able to submit wind speed readings (in knots) for a given anemometer at a
given time.
- A paginated endpoint featuring a list of anemometers with their 5 latest readings, and the
anemometer’s weekly/daily speeds
- Users are able to see the daily/weekly mean wind speed for each anemometer.
- Users are able to list all paginated readings for a given anemometer.
- Users are able to filter anemometer readings according to a given set of tags.
- Authentication is required to call the API.

# Getting started

## Installing dependencies

You're going to need [docker](https://www.docker.com/) to run this project.

I firmly recommend you install [go-task](https://taskfile.dev/installation/) to run the project's tasks but if you wish to not use the util you may take a look at `taskfile.yml`and run them yourself.

The following will only regard Macos as I use one for work.

If you're running linux, replace the brew commands with your package manager.

At project root run:
```bash
task install-deps # Installs pre-commit, uv, ruff
```

## Tasks

These tasks are useful for running the project and utils for dev environment.

### List all "important" tasks:
```bash
task
````

**Note**: This will note list **all** tasks, simply the ones I added a description to, I deem interesting for an external dev. Feel free to take a look at all of them in `taskfile.yml`.

-----------------------------------------------------------

### Initialize the app
Idempotent task building, initializing and running the app:
```bash
task init-app
````
**Note**: Resets all data and tables. There will be one user, 50 anemometer each with 100 readings bundled. If you wish to retain data after that, use `task up` instead.

Put [0.0.0.0:8000](http://0.0.0.0:8000/) in your browser to go on the frontpage.

This will run the stack in detached mode (needed to run data initialization), if you wish for logs use `task up` or `task logs` after.

-----------------------------------------------------------

### Initialize a venv
If you wish to create a venv for local development instead of using a `devcontainer`:
```bash
task init-venv
````

Then select the venv though your ide or activate it in your terminal:
```bash
source .venv/bin/activate
````
-----------------------------------------------------------

### Reset DB
Empty DB & run migrations, useful if you wish for a clear DB state:
```bash
task reset-db
````
-----------------------------------------------------------
### Generate anemometers
Create anemometers with a set of readings
```bash
task create_anemometers -- num_of_anemometers num_of_readings_per_anemometers num_tags_per_reading
# ex: task create_anemometers -- 50 100 2
````

-----------------------------------------------------------
### Running tests
```bash
task tests
````

-----------------------------------------------------------
### Any django management command
```bash
task manage -- management_command
# ex: task manage -- collectstatic
````

## Docs

There is a sphinx documentation, nothing much in there but generated skeleton from docstrings and prototypes, can serve for future enduser documentation.

```bash
task docs-up
````

Go to [0.0.0.0:9000](http://0.0.0.0:9000/) after the command to access it.

To stop it:
```bash
task docs-down
````
