from langchain import chains
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_core import language_models
from pinecone import Pinecone as PineconeClient


class RetrievalQa:
    def __init__(
        self,
        llm: language_models.BaseChatModel,
        index_name: str,
        embedding_model_name: str,
        openai_api_key: str,
        text_key: str,
        pinecone_api_key: str,
    ) -> None:
        self._llm = llm
        embed = OpenAIEmbeddings(
            model=embedding_model_name, openai_api_key=openai_api_key
        )
        pc = PineconeClient(api_key=pinecone_api_key)
        index = pc.Index(index_name)
        self._vectordb = Pinecone(index, embed.embed_query, text_key)

    def get_chain(self) -> chains.RetrievalQA:
        qa = chains.RetrievalQA.from_chain_type(
            llm=self._llm,
            chain_type="stuff",
            retriever=self._vectordb.as_retriever(),
        )
        return qa
