const num1Input = document.getElementById('num1');
const num2Input = document.getElementById('num2');
const operatorSelect = document.getElementById('operator');
const calculateBtn = document.getElementById('calculate-btn');
const resultElement = document.getElementById('result');
const showHistoryBtn = document.getElementById('show-history-btn');
const historyList = document.getElementById('history-list');

calculateBtn.addEventListener('click', () => {
    const num1 = parseFloat(num1Input.value);
    const num2 = parseFloat(num2Input.value);
    const operator = operatorSelect.value;

    if (isNaN(num1) || isNaN(num2)) {
        resultElement.textContent = 'Result: Invalid input';
        return;
    }

    let result;
    switch (operator) {
        case '+':
            result = num1 + num2;
            break;
        case '-':
            result = num1 - num2;
            break;
        case '*':
            result = num1 * num2;
            break;
        case '/':
            if (num2 === 0) {
                resultElement.textContent = 'Result: Cannot divide by zero';
                return;
            }
            result = num1 / num2;
            break;
    }

    resultElement.textContent = `Result: ${result}`;

    // Send the calculation to the Python server
    saveCalculation(num1, num2, operator, result);
});

async function saveCalculation(num1, num2, operator, result) {
    try {
        const response = await fetch('http://127.0.0.1:5000/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                num1: num1,
                num2: num2,
                operator: operator,
                result: result
            })
        });
        
        const data = await response.json();
        console.log(data.message);
        
    } catch (error) {
        console.error('Error saving calculation:', error);
    }
}

showHistoryBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('http://127.0.0.1:5000/history');
        const history = await response.json();

        historyList.innerHTML = ''; // Clear previous history
        if (history.length === 0) {
            historyList.textContent = 'No calculation history.';
            return;
        }

        history.forEach(item => {
            const historyItem = document.createElement('p');
            historyItem.textContent = `${item.calculation} = ${item.result} (${new Date(item.timestamp).toLocaleString()})`;
            historyList.appendChild(historyItem);
        });

    } catch (error) {
        console.error('Error fetching history:', error);
        historyList.textContent = 'Error loading history.';
    }
});