import os
from dotenv import load_dotenv
import streamlit as st

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

st.set_page_config(
    page_title='Estoque GPT',
    page_icon=':page_facing_up:',
)

st.header('Assistente de Estoque')

model_options = [
    'gpt-3.5-turbo',
    'gpt-4',
    'gpt-4-turbo',
    'gpt-4o-mini',
    'gpt-4o',
]

selected_model = st.sidebar.selectbox(
    label='Selecione o modelo LLM',
    options=model_options
)

st.sidebar.markdown('### Sobre')
st.sidebar.markdown('Este agente consulta um banco de dados de estoque utilizando um modelo GPT')

st.write('Faça perguntas sobre o estoque de produtos, preços e reposições.')
user_question = st.text_input('O que deseja saber sobre o estoque?')

model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=selected_model,
)

db = SQLDatabase.from_uri('sqlite:///estoque.db')

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=model
)

system_message = hub.pull('hwchase17/react')

agent = create_react_agent (
    llm=model,
    tools=toolkit.get_tools(),
    prompt=system_message,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=toolkit.get_tools(),
    verbose=True,
    handle_parsing_errors=True
)

prompt = '''
Use as ferramentas necessárias para responder as perguntas relacionadas ao estoque de produtos. Você fornecerá insights sobre produtos, preçis e reposição de estpque e relatórios conforme solicitado pelo usuário.
A resposta final deve ter uma formatação amigpavel de visualização para o usuário. Sempre responda em Português.
Pergunta: {q}
'''

prompt_template = PromptTemplate.from_template(prompt)



if st.button('Consultar'):
    if user_question:
        formatted_template = prompt_template.format(q=user_question)
        output = agent_executor.invoke({'input': formatted_template})
        st.markdown(output.get('output'))
    else:
        st.warning('Por favor, faça uma pergunta.')