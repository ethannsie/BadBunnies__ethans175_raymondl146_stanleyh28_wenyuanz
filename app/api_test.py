# from google import genai
# from google.genai import types

with open('keys/key_gemini.txt', 'r') as file:
    gemini_key = file.readline().strip()

# client = genai.Client(api_key=gemini_key)

# response = client.models.generate_content(
#     model="gemini-2.5-flash-preview-05-20",
#     config=types.GenerateContentConfig(
#         system_instruction="I don't want the sentence meaning or structure to be changed at all, simply fix grammar and guess what word the user is trying to say. I only want the corrected sentence."),
#     contents="What is this person trying to say: Because the carthinks loudly, we can't umbrella without frogs."
# )

# print(response.text)

from google import genai

client = genai.Client(api_key=gemini_key)

my_file = client.files.upload(file="test2/test2.jpg")

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-05-20",
    contents=[my_file, "Extract text from this image, return just the text extracted."],
)

print(response.text)