from django.contrib.auth.hashers import Argon2PasswordHasher as BaseArgon2PasswordHasher

class Argon2PasswordHasher(BaseArgon2PasswordHasher):
    time_cost = 8
    memory_cost = 32768
    parallelism = 2
