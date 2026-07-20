class DatasetGenerationAgent:

    def __init__( self, question_agent, retrieval_agent, sql_agent, validation_agent, writer_agent ):

        self.question_agent = question_agent

        self.retrieval_agent = ( retrieval_agent )

        self.sql_agent = sql_agent

        self.validation_agent = ( validation_agent )

        self.writer_agent = ( writer_agent )


    async def run( self ,metadata, datasource, count=30):

        retrieval_dataset = []

        generation_dataset = []

        questions = await ( self.question_agent.generate(metadata, count) )

        for item in questions:

            question = (item["question"])

            retrieval = await ( self.retrieval_agent.generate(question,metadata))

            sql = await (self.sql_agent.generate(question,retrieval["expected_tables"],metadata))

            valid = await (self.validation_agent.validate(sql["gold_sql"],datasource) )

            if not valid:
                continue

            retrieval_dataset.append({
                    "question": question,
                    "expected_tables": retrieval["expected_tables"]
                })

            generation_dataset.append({
                    "question":question,
                    "expected_tables": retrieval["expected_tables"],
                    "gold_sql": sql["gold_sql"]
                })

        await ( self.writer_agent.save( datasource, retrieval_dataset, generation_dataset) )
        return {
            "retrieval": retrieval_dataset,
            "generation": generation_dataset
        }