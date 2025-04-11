function show_elements(selector) {
	if (document.querySelector(selector).style.display == "none") {
		document.querySelector(selector).style.display = "block";
	} else {
		document.querySelector(selector).style.display = "none";
	}
}
function copy_to_clipboard(link) {
	navigator.clipboard.writeText(link)
}
function add_to_favorites() {
	const tasks = document.querySelectorAll('.add_to_favorite');
	const like = "/static/img/like.png";
	const unlike = "/static/img/unlike.png";
	tasks.forEach(task => {
		task.addEventListener('click', () => {
			let like_btn = task.querySelector('.like');
			if (like_btn.src == like) {
				like_btn.src = unlike;
			} else {
				like_btn.src = like;
			};
			task.classList.add('active');
			setTimeout(() => {
				task.classList.remove('active');
			}, 200);

			let url = '/users/favorites/';
			const data = {
				'task_id': task.id,
			};
			fetch(url, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrf_token,
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(data),
			});
		});
	});
}
function delete_from_favorites() {
	const rows = document.querySelectorAll('.delete_from_favorite');
	const url = '/users/favorites/';
	rows.forEach(row => {
		let delete_btn = row.querySelector('td > a');
		let task_id = delete_btn.id;
		delete_btn.addEventListener('click', () => {
			row.remove();
			const data = {
				'task_id': task_id,
			};
			fetch(url, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrf_token,
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(data),
			});
		})
	});
}
function open_modal_window() {
	const tasks = document.querySelectorAll('.add_to_tests');
	if (tasks) {
		const close_btn = document.querySelector('.close-btn');
		const modal_window = document.querySelector('.modal-window');
		const save_button = document.querySelector('.save-button');
		const url = '/tests/create-test/';
		tasks.forEach(task => {
			task.addEventListener('click', () => {
				if (save_button) {
					save_button.id = task.id
				}
				modal_window.classList.toggle('hidden');
			})
		});
		if (close_btn) {
			close_btn.addEventListener('click', () => {
				modal_window.classList.toggle('hidden');
			})
		}
		if (save_button) {
			save_button.addEventListener('click', () => {
				modal_window.classList.toggle('hidden');
				let chosen_tests = document.querySelectorAll('.chosen-tests');
				let data = {
					'task_id': save_button.id,
				};
				for (let i = 0; i < chosen_tests.length; i++) {
					test_id = chosen_tests[i].id
					data[test_id] = chosen_tests[i].checked;
					chosen_tests[i].checked = false;
				}
				fetch(url, {
					method: 'POST',
					headers: {
						'X-CSRFToken': csrf_token,
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(data),
				});
			})
		}
		
	}
}
function test_info() {
	const test_id = document.querySelector('#test_id').name;
	const publish_button = document.querySelector('#publish_button');

	const solvings = document.querySelectorAll('.solving');
	if (solvings) {
		solvings.forEach(solving => {
			solving.addEventListener('click', () => {
				window.location.href = '/test-result/' + solving.dataset.testid;
			})
		})
	}
	const delete_btns = document.querySelectorAll('.delete_from_test > td > a');
	if (delete_btns) {
		delete_btns.forEach(delete_btn => {
			let url = '/tests/delete-task-from-test/' + test_id;
			let task_id = row.dataset.task_id;
			delete_btn.addEventListener('click', () => {
				row.remove();
				if (rows.length == 1) {
					publish_button.classList.toggle('hidden');
				}
				const data = {
					'task_id': task_id,
				};
				fetch(url, {
					method: 'POST',
					headers: {
						'X-CSRFToken': csrf_token,
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(data),
				});
			})
		});
	}
	if (publish_button) {
		publish_button.addEventListener('click', () => {
			let url = '/tests/publish-test/' + test_id;
			window.location.href = url;
			fetch(url, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrf_token,
					'Content-Type': 'application/json',
				}
			});
		})
	}
	
}
function my_tests() {
	const tests = document.querySelectorAll('.test');
	tests.forEach(test => {
		const delete_btn = test.querySelector('.delete-link');
		delete_btn.addEventListener('click', () => {
			test.remove();
			let url = '/tests/delete-test/' + delete_btn.id;
			fetch(url, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrf_token,
					'Content-Type': 'application/json',
				}
			});
		})
	});
}
function open_link_with_params(params, values) {
	if (window.history && history.pushState) {
		history.pushState({foo: 'bar'}, 'Title', location.href.replace(location.hash,''));
	}
	const currentUrl = new URL(window.location.href);
	for (let i = 0; i < params.length; i++) {
		currentUrl.searchParams.set(params[i], values[i]);
	}
	window.location.href = currentUrl;
}
function checkbox_function(main_checkbox, inputs_id) {
	if (main_checkbox.checked == true) {
		var list = document.getElementsByClassName(inputs_id);	
		for (let i = 0; i < list.length; i++) {
			list[i].checked = true;
		}
	} else {
		var list = document.getElementsByClassName(inputs_id);	
		for (let i = 0; i < list.length; i++) {
			list[i].checked = false;
		}
	}
}
function check_checkbox_status(checkboxes_class, main_checkbox_id) {
	var list = document.getElementsByClassName(checkboxes_class);
	for (var i = 0; i < list.length; i ++) {
		if (list[i].checked) {
			true;
		}
		else {
			document.getElementById(main_checkbox_id).checked = false;
			return 0;
		}
	}
	document.getElementById(main_checkbox_id).checked = true;
}
function lessexercises(input_id) {
	var value = Number(document.getElementById(input_id).value);
	if (value > 0) {
		value -= 1;
	}
	document.getElementById(input_id).value = value;
	ready_button();
}
function moreexercises(input_id) {
	var value = Number(document.getElementById(input_id).value);
	if (value >= 0) {
		value += 1;
	}
	document.getElementById(input_id).value = value;
	ready_button();
}
function first_part(input) {
	var inputs = document.querySelectorAll('.topic1 > .tel-input')
	if (input.checked) {
		for (var i = 0; i < inputs.length; i++) {
			inputs[i].value = 1;
		}
		ready_button();
	} else {
		for (var i = 0; i < inputs.length; i++) {
			inputs[i].value = 0;
		}
		ready_button();
	}
	
}
function second_part(input) {
	var inputs = document.querySelectorAll('.topic2 > .tel-input')
	if (input.checked) {
		for (var i = 0; i < inputs.length; i++) {
			inputs[i].value = 1;
		}
		ready_button();
	} else {
		for (var i = 0; i < inputs.length; i++) {
			inputs[i].value = 0;
		}
		ready_button();
	}
}
function ready_button() {
	var list = document.getElementsByClassName("tel-input");
	var count = 0;
	for (var i = 0; i < list.length; i++) {
		count += Number(list[i].value);
	}
	document.querySelector('span#ready-button').textContent = count;
}
function chosed_input_check() {
	list = document.getElementsByClassName('tel-input');
	for (var i = 0; i < list.length; i++) {
		list[i].addEventListener('input', ready_button);
	}
}
function sort() {
	const urlString = window.location.href;
	const url = new URL(urlString);

	const selectElement = document.querySelector('#sort-select');
	if (selectElement) {
		const options = selectElement.options;
		const showed = url.searchParams.get('sorted');
		if (showed) {
			for (let i = 0; i < selectElement.length; i++) {
				options[i].removeAttribute('selected');
				if (options[i].value == showed) {
					options[i].setAttribute('selected', 'selected')
				}
			}
		}
	}
	
}
function selected_options_sort() {
	const urlString = window.location.href;
	const url = new URL(urlString);

	sort_options = document.querySelectorAll('.showed-box > a')
	sort_options.forEach( sort_option => {
		const showed = url.searchParams.get('showed');
		if (showed == sort_option.textContent) {
			sort_option.classList.add('chosen-sort');
		}
	})
}
document.addEventListener("DOMContentLoaded", () => {
	chosed_input_check();
	sort();
	selected_options_sort();
	add_to_favorites();
	delete_from_favorites();
});