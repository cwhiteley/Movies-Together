from faker import Faker


async def get_user(cokies: dict):
    if cokies.get("access_token"):
        return "user_form_token"
    return Faker().first_name()
