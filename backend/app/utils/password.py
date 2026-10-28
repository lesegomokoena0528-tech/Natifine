import bcrypt


class PasswordUtil:

    @staticmethod
    def hash(password: str):

        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

    @staticmethod
    def verify(password, hashed):

        return bcrypt.checkpw(
            password.encode(),
            hashed.encode()
        )