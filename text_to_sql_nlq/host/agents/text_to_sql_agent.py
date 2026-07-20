from graph.workflow import compiled_workflow
from graph.state import RequestContext

class TextToSQLAgent:
    async def run(self, question: str, datasource: str, context: RequestContext, type: str) -> dict:
        initial_state = {
            "question": question, 
            "context": context,
            "datasource": datasource, 
            "intent": "",
            "schema_context": {},
            "generated_sql": "", 
            "sql_result": [],
            "answer": "", 
            "error": None, 
            "retry_count": 0,
            "type": type
        }
        final_state = await compiled_workflow.ainvoke(initial_state)
        return {"answer": final_state.get("answer"), "generated_sql": final_state.get("generated_sql"), "result": final_state.get("sql_result")}