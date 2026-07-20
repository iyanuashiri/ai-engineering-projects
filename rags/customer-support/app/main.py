import os
import base64
import requests
from openai import OpenAI
from langsmith import traceable, Client, uuid7  
from langsmith.run_helpers import get_current_run_tree
from langsmith.wrappers import wrap_openai
from decouple import config


os.environ["LANGSMITH_API_KEY"] = config("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = config("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = config("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = config("LANGSMITH_ENDPOINT")

OPENROUTER_API_KEY = config("OPENROUTER_API_KEY")

client = wrap_openai(OpenAI(
    base_url="https://openrouter.ai/api/v1",
    # model="openai/gpt-5.4-mini",
    api_key=OPENROUTER_API_KEY
))

docs = [
    "Acme Cloud supports unlimited users on Enterprise plans. Starter plans are limited to 5 users.",
    "To reset your password, click 'Forgot password' on the login page and follow the instructions sent to your email.",
    "API rate limits are 1,000 requests per hour on the Starter plan and 10,000 requests per hour on Enterprise.",
]

@traceable(run_type="retriever")
def retriever(query: str) -> list[str]:
    return docs


@traceable(run_type="llm", name="Support Bot", tags=["support-bot-tag"], metadata={"ls_model_name": "openai", "ls_model_name": "gpt-5.4-mini"})
# @traceable
def support_bot(question: str) -> str:
    run = get_current_run_tree()
    print(f"format_prompt Run Id: {run.id}")
    print(f"format_prompt Trace Id: {run.trace_id}")
    # print(f"format_prompt Parent Run Id: {run.parent_run.id}")
    context = retriever(question)
    system_message = (
        "You are a helpful customer support agent. "
        "Answer using only the information provided below:\n\n"
        + "\n".join(context)
    )
    response = client.chat.completions.create(
        model="openai/gpt-5.4-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
    )

    token_usage = {
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        # "input_tokens_cost": response.usage.cost_details['upstream_inference_prompt_cost'],
        # "output_tokens_cost": response.usage.cost_details['upstream_inference_completions_cost'],
        # "total_tokens_cost": response.usage.cost,
        # "input_token_details": {"cache_read": 10}
    }

    # token_usage = {
    #     "input_tokens": run.prompt_tokens,
    #     "output_tokens": run.completion_tokens,
    #     "total_tokens": run.total_tokens,

    # }
    run.set(usage_metadata=token_usage)

    # print(response.usage.completion_tokens)
    # print(response.usage.prompt_tokens)
    # print(response.usage.total_tokens)
    # print(response.usage.cost)
    # print(response.usage.cost_details['upstream_inference_cost'])
    # print(response.usage.cost_details['upstream_inference_prompt_cost'])
    # print(response.usage.cost_details['upstream_inference_completions_cost'])

    # print(run)

    return response.choices[0].message.content, run.trace_id
    # return response, run.trace_id 

if __name__ == "__main__":
    ##################### If You Need Trace #######################
    # print(support_bot("How many users can I have on the Starter plan?"))

    ##########################If You Need User Feedback plus Trace #############################
    run_id = str(uuid7())
    # run = get_current_run_tree()
    response, trace_id = support_bot(
        "How many users can I have on the Starter plan?",
        langsmith_extra={"run_id": run_id},
    )
    ls_client = Client()
    ls_client.create_feedback(trace_id, key="user-score", score=1.0)

    ####################################################################

# direct_image_url = "https://upload.wikimedia.org/wikipedia/commons/d/d7/Cristiano_Ronaldo_playing_for_Al_Nassr_FC_against_Persepolis%2C_September_2023_%28cropped%29.jpg"

# # 1. Add a standard browser User-Agent header
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# }

# # 2. Pass the headers into the get request
# img_response = requests.get(direct_image_url, headers=headers)
# img_response.raise_for_status() 

# # 3. Convert and format
# image_base64 = base64.b64encode(img_response.content).decode('utf-8')
# data_uri = f"data:image/jpeg;base64,{image_base64}"


# @traceable(run_type="llm", name="Image Detail", tags=["image-detail-tag"], metadata={"my-key": "my-value"})
# def get_detail_of_image():
#     run = get_current_run_tree()
#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "What's in this image?"},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": data_uri, 
#                         },
#                     },
#                 ],
#             }
#         ],
#     )
#     result = response.choices[0].message.content
#     run.metadata["image-detail"] = result
#     ls_client = Client()
#     ls_client.create_feedback(run.trace_id, key="image-score", score=1.0)


# get_detail_of_image()