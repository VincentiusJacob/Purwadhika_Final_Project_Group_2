import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

load_dotenv()

st.set_page_config(page_title="Job Search Chatbot", layout="centered")

st.title("Job Search Assistant")
st.write("Tanya apapun tentang pekerjaan di Indonesia")

api_key = os.getenv("OPENAI_API_KEY")
qdrant_url = os.getenv("QDRANT_ENDPOINT") 
qdrant_api_key = os.getenv("QDRANT_API_KEY")  
collection_name = "Jobs_Documents" 

if not api_key:
    st.warning("OPENAI API KEY Belum Ada...")
    st.stop()


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
)


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

@st.cache_resource
def init_qdrant():
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key
    )

    vectorstore = QdrantVectorStore(
        client,
        collection_name,
        embeddings,
    )

    return vectorstore

try:
    vectorstore = init_qdrant()
except Exception as e:
    st.error(f"Gagal koneksi ke Qdrant: {e}")
    st.stop()


if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="""
                        Kamu adalah asisten pencari kerja di Indonesia. 
                        Gunakan informasi dari context yang diberikan untuk menjawab pertanyaan pengguna.
                        Jika informasi tidak ada di context, katakan dengan jujur bahwa kamu tidak menemukan informasi tersebut.
                      """)
    ]


for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)


if prompt := st.chat_input("Cari pekerjaan atau tanya seputar karir..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append(HumanMessage(content=prompt))


    with st.chat_message("assistant"):

        with st.status("Menganalisis pertanyaan...", expanded=True) as status:
            
            check_prompt = f"""
                Apakah pertanyaan ini memerlukan pencarian informasi pekerjaan di database? 
                Pertanyaan: "{prompt}"

                Jawab hanya dengan: YES atau NO
                """
            
            need_retrieval = llm.invoke([HumanMessage(content=check_prompt)])
            needs_db = "yes" in need_retrieval.content.lower()
            
            if needs_db:
                st.write("Pertanyaan terkait pekerjaan, akan dilakukan analisis database")
            else:
                st.write("Pertanyaan umum")
            
            status.update(label="Analisis selesai", state="complete")
        

        context_docs = []
        if needs_db:
            with st.status("Mencari di database...", expanded=True) as status:
                st.write(f"Mencari dokumen relevan untuk: *'{prompt}'*")
                
                try:
        
                    retriever = vectorstore.as_retriever(
                        search_kwargs={"k": 3}
                    )
                    context_docs = retriever.invoke(prompt)
                    
                    st.write(f"Ditemukan **{len(context_docs)} dokumen** relevan")
                    
       
                    with st.expander("Lihat dokumen yang ditemukan"):
                        for i, doc in enumerate(context_docs, 1):
                            st.markdown(f"**Dokumen {i}:**")
                            st.text(doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content)
                            st.divider()
                    
                    status.update(label="Pencarian selesai", state="complete")
                    
                except Exception as e:
                    st.error(f"Error saat retrieve: {e}")
                    status.update(label="Pencarian gagal", state="error")
        

        with st.status("Menyusun jawaban...", expanded=False) as status:
            
            if context_docs:
           
                context = "\n\n".join([doc.page_content for doc in context_docs])
                
      
                rag_prompt = f"""
                Berdasarkan informasi berikut dari database:

                {context}

                Pertanyaan user: {prompt}

                Berikan jawaban yang informatif dan relevan. Jika informasi tidak cukup, katakan dengan jujur.
                """
                
                final_messages = st.session_state.messages[:-1] + [HumanMessage(content=rag_prompt)]
            else:
  
                final_messages = st.session_state.messages
            
    
            response = llm.invoke(final_messages)
        

        st.markdown("### 💬 Jawaban:")
        st.markdown(response.content)
    

    st.session_state.messages.append(AIMessage(content=response.content))


