from django.contrib.auth.hashers import Argon2PasswordHasher as BaseArgon2PasswordHasher

class Argon2PasswordHasher(BaseArgon2PasswordHasher):
    time_cost = 2
    memory_cost = 32768
    parallelism = 3
