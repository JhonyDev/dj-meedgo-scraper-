def get_platform_dict():
    from core.settings import PLATFORMS
    return {name: num for num, name in PLATFORMS}
