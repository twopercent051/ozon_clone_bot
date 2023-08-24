try:
    a = int("q")
except Exception as ex:
    print(ex.__traceback__.tb_frame)
