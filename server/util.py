import random
import string


def random_string(length):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(alphabet) for _ in range(length))
