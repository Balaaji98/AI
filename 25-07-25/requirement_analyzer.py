from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

def analyze_requirements_with_local_model(extracted_text):
    """
    Analyzes the extracted text to identify key requirements and provide detailed development recommendations
    using a smaller, faster Hugging Face model locally with 8-bit quantization.
    
    Args:
        extracted_text (str): The text extracted from the requirement document.
    
    Returns:
        str: Analyzed requirements and detailed development recommendations.
    """
    try:
        # Load a smaller, faster model and tokenizer with 8-bit quantization
        model_name = "distilgpt2"  # Smaller model for faster inference
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)

        # Refined input prompt for development recommendations
        prompt = f"""
        You are an expert in warehouse management systems (WMS), specifically Blue Yonder Dispatcher 2019 WMS. 
        Analyze the following requirement text and provide:
        1. Key requirements.
        2. Affected WMS components (e.g., PL/SQL packages, RDT rules, database tables).
        3. Detailed development recommendations for implementing the changes, including:
           - What changes need to be made to PL/SQL packages.
           - What updates are required in RDT rules.
           - Any database schema changes or new tables required.
           - Testing strategies to validate the changes.

        Requirement Text:
        {extracted_text}

        Provide your response in a structured format with clear sections for each point.
        """

        # Tokenize and generate output
        inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
        inputs = inputs.to(device)
        outputs = model.generate(inputs["input_ids"], max_length=500, temperature=0.7)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    except Exception as e:
        print(f"Error analyzing requirements: {e}")
        return ""

# Test the function with the extracted text
if __name__ == "__main__":
    from input_parser import extract_text_from_docx

    # Path to the sample requirement document
    file_path = '/Users/balaajiganesh/Library/Mobile Documents/com~apple~CloudDocs/WMS-AI-DESIGN-AGENT/sample_requirement.docx'
    extracted_text = extract_text_from_docx(file_path)

    # Analyze the requirements locally
    analyzed_requirements = analyze_requirements_with_local_model(extracted_text)
    print("Analyzed Requirements and Detailed Development Recommendations:\n")
    print(analyzed_requirements)