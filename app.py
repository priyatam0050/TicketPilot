import streamlit as st
from models import TicketStore
from rag import answer_question
st.title("Ticket Pilot")

sel_res=[]
kb_tag,kb_tickets=st.tabs(["ASK KB","Tickets"])
with kb_tag:
    question=st.text_input("Ask a support Question")
    btn=st.button("ASK")
    if btn:
        if question.strip()=='':
            st.warning("Please enter a valid question")
        else:
            with st.spinner("Searching KB....."):
                answer=answer_question(question)
            st.markdown(answer["answer"])
            if answer["sources"]:
                st.caption("Sources : "+",".join(answer["sources"]))
            
with kb_tickets:
    ticket=TicketStore()
    result=ticket.list_tickets()
    selected=st.selectbox("priority",["ALL","P1","P2","P3","P4"])
    
    if selected!='ALL':
        for i in result:
            if i["Priority"]==selected:
                sel_res.append(i)
        result=sel_res
    
    st.dataframe((result))
    st.metric("Total",str(len(result)))
    
