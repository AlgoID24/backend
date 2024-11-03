import strawberry


@strawberry.input
class EmailPasswordSignUpInput:
    email: str
    password_1: str
    password_2: str


@strawberry.input
class EmailPasswordSignInInput:
    email: str
    password: str
