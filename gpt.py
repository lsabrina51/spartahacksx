import random
import argparse
import os
from openai import OpenAI

# Initialize the OpenAI client
# It's better to use environment variables for API keys rather than hardcoding them
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def read_input_file(file_path):
    """Read and return the contents of the input file."""
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading input file: {e}")

def determine_mood(input_text):
    """Determine whether the response should be 'good' or 'evil' based on input text."""
    if 'good' in input_text.lower():
        return 'good'
    elif 'evil' in input_text.lower():
        return 'evil'
    else:
        return random.choice(['good', 'evil'])

def get_gpt3_response(mood, text):
    """Get response from GPT-3.5 based on the mood."""
    system_message = "You are an assistant that can respond in different moods."
    
    if mood == 'evil':
        user_prompt = (
            "Respond in a mean, unhelpful way (while keeping it appropriate and not harmful). "
            f"The question is: {text}"
        )
    else:
        user_prompt = (
            "Respond in a kind, supportive, and encouraging way. "
            f"The question is: {text}"
        )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        # Updated response parsing for the current API version
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error generating response: {e}")

def generate_response(file_path):
    """Generate the full response with mood tag."""
    try:
        input_text = read_input_file(file_path)
        mood = determine_mood(input_text)
        gpt3_response = get_gpt3_response(mood, input_text)
        return f"[{mood.upper()}] {gpt3_response}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function to handle command-line execution."""
    parser = argparse.ArgumentParser(
        description="Generate GPT-3.5 responses with different moods based on input text."
    )
    parser.add_argument(
        "file_path",
        help="Path to the input text file"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (alternatively, set OPENAI_API_KEY environment variable)",
        default=os.getenv('OPENAI_API_KEY')
    )

    args = parser.parse_args()

    # Set API key if provided via command line
    if args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key

    # Verify API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OpenAI API key not found. Please provide it via --api-key or set the OPENAI_API_KEY environment variable.")
        return

    try:
        response = generate_response(args.file_path)
        print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()