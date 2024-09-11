from locust import HttpUser, TaskSet, task, between

class ProductTasks(TaskSet):
    @task
    def load_products_grid(self):
        # Simula el acceso a la vista "grid" de ProductoView
        self.client.get("/inventario/api/v1/producto/grid/?limit=10&offset=0")

class UserTasks(TaskSet):
    @task
    def login(self):
        # Simula el acceso a la vista de login
        self.client.post(
            "/users/api/v1/login/", json={"username": "admin", "password": "1234"}
        )

class WebsiteUser(HttpUser):
    tasks = [ProductTasks, UserTasks]
    wait_time = between(1, 5)
