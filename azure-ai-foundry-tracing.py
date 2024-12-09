import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from dotenv import load_dotenv
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

from langsmith import Client

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')

load_dotenv()

exporter = AzureMonitorTraceExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)

span_processor = BatchSpanProcessor(exporter, schedule_delay_millis=60000)
tracer_provider.add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

from openinference.instrumentation.langchain import LangChainInstrumentor
LangChainInstrumentor().instrument()

from langchain_openai import AzureChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "What is the weather ?"),
])

llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",
        model="gpt-4o-mini",
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        temperature=0,
        max_retries=5,
        max_tokens=4000
    )

chain = prompt | llm

response = chain.invoke({"input": "What is the weather in San Francisco?"})
print(response)

