    function showQuestion() {
            document.getElementById('question-div').classList.remove('hidden');
            document.getElementById('solution-div').classList.add('hidden');
        }

        function showSolution() {
            document.getElementById('question-div').classList.add('hidden');
            document.getElementById('solution-div').classList.remove('hidden');
        }