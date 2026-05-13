from datetime import datetime


def main() -> None:
    now = datetime.now().isoformat(timespec="seconds")
    print(f"starter-project python app running: {now}")


if __name__ == "__main__":
    main()