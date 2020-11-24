def get_router(number, content):
    if 'OTP' in content:
        return 'default'
    else:
        return 'dummy'
