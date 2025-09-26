from main import MyAI

# TEST
def main():
    # Create a 4x4x4 cube filled with 0
    cube = [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    
    ai = MyAI()
    result = ai.get_move(cube, 1, [0, 0, 0])

    print("Result of :", result)  # Expected output:
if __name__ == "__main__":
    main()