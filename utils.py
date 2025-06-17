import streamlit as st
import re
from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig,TextIteratorStreamer
import threading

def chat1(model,tok,question=None):
    if(question==None):
        question=input("Give your question :: ")
    message = [
    {
        "role": "system",
        "content": """
You are a helpful assistant. You perform **only one** of the following tasks based on the user's input:

---

### 🔑 IMPORTANT TERMS

- **MULTIQUERY**: A request that includes **more than one clearly distinct task**.
    - Example: “Make a PDF on AI and another one on ML” → This is a MULTIQUERY.
    - Example: “Generate 3 PDFs on AI, ML, and DL” → This is a MULTIQUERY.
    - NOT a MULTIQUERY: “Generate a PDF on kites.” ← This is a single task.
- **Single Task**: Any prompt that contains only one action, even if the topic has subparts (e.g., “types of kites”).
- **Never guess or add tasks** not directly requested by the user.
    - ❌ Never turn “PDF on kite” into two tasks like “PDF on kite” and “PDF on types of kite.”
    - ❌ Never say “future of AI” unless user says so.

---

**STEP 1: MULTIQUERY (If the user asks for more than one task)**

If the user is asking for two or more distinct tasks (e.g., multiple documents or actions):

- STOP. Do NOT answer the question or generate content.
- Return a Python-style list of strings inside a <multiquery></multiquery> tag.

Format:

```python
<multiquery>
[
  "Task 1 in plain English.",
  "Task 2 in plain English."
]
</multiquery>

Only use this if there are **two or more explicit actions**. If only one action is present, continue to Step 2.

---

**STEP 2: DOCUMENT GENERATION**

If the user is asking for **one document only** (like "Generate a PDF on X"):
- Return a structured document with these parts:
  - A title in this format: `<title>Your Title</title>`
  - Rich, multi-paragraph content (Introduction, Details, Conclusion)
  - Exactly one of the following tags:
    - `<DownloadPDF>` for PDFs
    - `<DownloadDOCX>` for Word files
- Do NOT include <multiquery> or chatbot-like replies.

If no document is asked for, continue to Step 3.

---

**STEP 3: REGULAR RESPONSE**

If the user is asking a **general question** (e.g., "What is AI?", "Explain machine learning", "Define deep learning"):
- Give a normal, helpful answer.
- DO NOT include <multiquery>, <title>, or download tags.
- Just respond clearly and concisely.

---

**RULES:**
- Always check for MULTIQUERY first — only if there are **2+ clear tasks**.
- Never mix steps. Only one step should be followed.
- Never return content when <multiquery> is used.
- NEVER guess what the user "might also want" — only act on clear instructions.
- Never add additional tasks by yourself
"""
    },
    {
        "role": "user",
        "content": question
    }
]
    prompt=tok.apply_chat_template(message,tokenize=False)
    tok_prompt=tok(prompt,return_tensors='pt').to('cuda')
    
    streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)
    generation_kwargs = dict(tok_prompt, streamer=streamer, max_new_tokens=4096)
    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    output_container = st.empty()
    full_output = ""
    for token in streamer:
        full_output += token
        output_container.markdown(full_output)
    return full_output


def chat2(model,tok,question=None):
    if(question==None):
        question=input("Give your question :: ")
    message=[
        {
            "role": "system",
"content": f"""
You are a helpful assistant that provides concise, direct responses and can generate high-quality, detailed documents when asked.
**Important Rules:**
- DON'T THINK TOO MUCH
- ANSWER VERY FAST SWIFTLY
- Follow classification steps in order.DON'T RECHECK AGAIN AND AGAIN take decision swiftly while classify
- If MULTIQUERY is true, do NOT go to Step 2 or Step 3.
- For MULTIQUERY, never return title, content, or tag fields — only the list of user-style instructions.
- When generating a document, aim for **depth, clarity, and structure** to produce a meaningful document, not just a short summary and always give title inside <title></title>.
- Generate document only if USER EXPLICITLY ASK TO GENERATE , NEVER ASSUME TO GENERATE DOCUMENT OR PDF BY YOURSELF.
**Classification Steps:**

**Step 1: MULTIQUERY Check**
    - If the user asks to perform more than one task in a single prompt (e.g., "Make a PDF on X and a Word on Y" or "Generate a DOCX and also explain Y"), classify as MULTIQUERY.
    - If MULTIQUERY is detected, STOP here and return:
    - A Python list of strings (STRICTLY) like ['Task1','Task2'].Note:- rewrite Task1 and Task2 then append in list,
    - Each string should clearly describe one task or document, such as:
        "Generate a DOCX file having information about the solar system."
    - Wrap the list inside a single <multiquery> tag
    - Do NOT proceed to Step 2 or Step 3

**Step 2: DOCUMENT_GENERATION Check**
    1. Create a relevant title wrapped in <title></title> (Always give title inside this tag STRICTLY)
    2. Generate **rich, informative, multi-paragraph content** that:
        - Covers the topic in depth,
        - Flows logically with clear sections (e.g., Introduction, Details, Examples, Conclusion),
        - Is **at least one page worth of text**,
        - Should be Professionally Written
        - DON'T OVERTHINK AND RESPOND AS FAST AS POSSIBLE
    3. End with exactly one tag:
        - <DownloadPDF> for PDF requests
        - <DownloadDOCX> for Word requests
    4. Include ONLY: properly structured title, content, and tag

**Step 3: REGULAR_QUERY**
    - If it is not a document generation task, respond normally.
    - Do NOT return <title>, download tags, or <multiquery>

**Important Rules:**
- DON'T THINK TOO MUCH
- ANSWER VERY FAST SWIFTLY
- Follow classification steps in order. Don't recheck again and again take decision swiftly while classify
- If MULTIQUERY is true, do NOT go to Step 2 or Step 3.
- For MULTIQUERY, never return title, content, or tag fields — only the list of user-style instructions.
- When generating a document, aim for **depth, clarity, and structure** to produce a meaningful document, not just a short summary and always give title inside <title></title>.
- Generate document only if user say this in query never assume.
"""
        },
        {
            "role":"user",
            "content": question
        }
    ]

    prompt=tok.apply_chat_template(message,tokenize=False)
    # print(prompt)
    tok_prompt=tok(prompt,return_tensors='pt').to('cuda')
    
    streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)
    generation_kwargs = dict(tok_prompt, streamer=streamer, max_new_tokens=4096)
    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    output_container = st.empty()
    full_output = ""
    for token in streamer:
        # print(token, end="", flush=True)
        full_output += token
        output_container.markdown(full_output)
    return full_output


def clean_output(text):
    flag=-1
    ind1=text.find("<title>")
    ind2=text.find("</title>")
    title=None
    text_out=None
    if re.search(r"<DownloadPDF>(?![>\w])", text):
        flag=1
    elif re.search(r"<DownloadDOCX>(?![>\w])", text):
        flag=0
    elif re.search(r"</multiquery>(?![>\w])", text):
        flag=2
    if(flag!=-1):
        think=None
        title=title=text[ind1+len("<title>"):ind2]
        text_out=text[ind2+len("</title>"):]
    else:
        title=None
        text_out=text
    think=None
    return flag,think,title,text_out


def clean_output2(text):
    flag=-1
    ind1=text.find("<think>")
    ind2=text.find("</think>")
    title=None
    text_out=None
    # print(text[ind1+len("<think>"):ind2])
    if '<DownloadPDF>' in text[ind2:]:
        flag=1
        print(flag)
        print(text)
    elif "<DownloadDOCX>" in text[ind2:]:
        flag=0
    elif "</multiquery>" in text[ind2:]:
        flag=2
    if(flag!=-1):
        ind3=text[ind2:].find("<title>")
        ind4=text[ind2:].find("</title>")
        title=text[ind2+ind3+len("<title>"):ind2+ind4]
        text_out=text[ind2+ind4+len('</title>'):]
    else:
        text_out=text[ind2+len("</think>"):]
    think=text[ind1:ind2]
    return flag,think,title,text_out


def give_model():
    bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16"
    )
    tok=AutoTokenizer.from_pretrained(
        "meta-llama/Llama-3.1-8B-Instruct"
    )
    model=AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-3.1-8B-Instruct",
        device_map='auto',
        quantization_config=bnb_config,
    )
    return model,tok

def give_model_d():
    bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16"
    )
    tok=AutoTokenizer.from_pretrained(
        "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
    )
    model=AutoModelForCausalLM.from_pretrained(
        "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        device_map='auto',
        quantization_config=bnb_config,
    )
    return model,tok  
def return_list(text):
    ind1=text.find("<multiquery>")
    ind2=text.find("</multiquery")
    return eval(text[ind1+len("<multiquery>"):ind2].strip())

def output(model,tok,question=None):
    if('Qwen3ForCausalLM' in str(model)):
        out=chat2(model,tok,question)
        flag,think,title,text=clean_output2(out)
    else:
        out=chat1(model,tok,question)
        flag,think,title,text=clean_output(out)
    try:
        if(flag==-1):
            print("Flag",flag)
            st.markdown(text)
        elif(flag==2):
            li=return_list(text)
            for i in li:
                output(model,tok,i)
        else:
            st.markdown("Word" if flag==0 else "PDF")
            st.markdown("-"*50)
            st.markdown(think)
            st.markdown("-"*50)
            st.markdown(title)
            st.markdown("-"*50)
            st.markdown(text)
            st.markdown('-'*50)
            if(flag==0):
                st.session_state.files.append([title,'docx',text])
            elif(flag==1):
                st.session_state.files.append([title,'pdf',text])
        st.session_state.Response.append(question)
        st.session_state.model_response.append(text)
    except Exception as e:
        print("Error")
        print(e)
        st.markdown("Word" if flag==0 else "PDF")
        st.markdown("-"*50)
        st.markdown(think)
        st.markdown("-"*50)
        st.markdown(title)
        st.markdown("-"*50)
        st.markdown(text)
        st.markdown('-'*50)