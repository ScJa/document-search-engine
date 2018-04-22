### init

The initial scoring used: 
- Calculates the score based on the scoring method for both the topic and the document and multiplies them.
- Adds up scores for all words.
- Trec_eval scores significantly higher

### tf

The initial scoring used: 
- Calculates the score based on the scoring method for the document and the text frequency for the topic and multiplies them.
- Adds up scores for all words.
- Trec_eval scores higher than default but lower than init

### without

The initial scoring used: 
- Calculates the score based on the scoring method only for the the document.
- Adds up scores for all words.
- Trec_eval scores by far lowest
