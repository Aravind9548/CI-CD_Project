async function loadTasks() {
  const response = await fetch('../tasks.json');
  const tasks = await response.json();
  window.allTasks = tasks;
  displayTasks(tasks);
}

function displayTasks(tasks) {
  const list = document.getElementById('taskList');
  list.innerHTML = '';
  tasks.forEach(t => {
    const li = document.createElement('li');
    li.innerHTML = `<strong>${t.description}</strong> 
                    <div class="status">Status: ${t.status}</div>`;
    list.appendChild(li);
  });
}

function filterTasks(status) {
  if (status === 'all') displayTasks(window.allTasks);
  else displayTasks(window.allTasks.filter(t => t.status === status));
}

document.getElementById('addBtn').addEventListener('click', () => {
  const input = document.getElementById('taskInput');
  const task = input.value.trim();
  if (!task) return alert('Enter a task description!');
  alert('Use CLI to actually add tasks: task-cli add "' + task + '"');
  input.value = '';
});

loadTasks();
