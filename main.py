import os
from GigaChatIntagration import GigaChatIntegration

if __name__ == "__main__":
    GCI = GigaChatIntegration()
    GCI.get_token()
    GCI.get_models()
    print("1 - формат ответа на задачу\n"
          "2 - формат беседы с GPT\n"
          "3 - формат беседы с веб-интерфейсом")
    choice = input()
    if choice == '1':
        print(GCI.get_aswer_with_prompt())
    elif choice == '2':
        print('О чём поговорим? ("q" - выход)')
        print(GCI.conversation(input()))
    elif choice == '3':
        os.system(f"streamlit run {os.path.abspath('WebInterface.py')}")
    else:
        pass
