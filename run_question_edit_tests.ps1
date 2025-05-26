# Run comprehensive tests for the question editing functionality

# Run backend tests
echo "Running backend tests for question editing..."
cd c:/Users/sreen/learning/copilot-agent/planventure/planventure-ta-assessment
pytest tests/test_question_update_comprehensive.py -v

# Run frontend tests
echo ""
echo "Running frontend tests for question editing..."
cd c:/Users/sreen/learning/copilot-agent/planventure/planventure-web
npm test src/components/assessment/EditQuestion.test.jsx

echo ""
echo "Tests completed!"
