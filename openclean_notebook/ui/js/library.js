/*
 * Initial load to fetch dataset rows and list of available commands.
 */
function load_spreadsheet(div_id, data) {
    fetch_spreadsheet(div_id, {dataset: data, action: 'load'});
}


/*
 * Fake execute simple command and fetch rows for the resulting dataset.
 */
function exec_command(div_id, dataset, engine) {
    const column = $('#colSelect option:checked').val();
    const command = $('#cmdSelect option:checked').val();
    fetch_spreadsheet(
        div_id,
        {
            dataset: {name: dataset, engine},
            action: 'exec',
            command,
            args: {column}
        }
    );
}


/*
 * Send a command to the backend that (potentially executes a command and)
 * fetches dataset rows.
 */
function fetch_spreadsheet(div_id, data) {
    let comm = Jupyter.notebook.kernel.comm_manager.new_comm('spreadsheet');
    // Show loader while we are fetching the data and the list of available
    // commands.
    $('#loader').show()
    $(div_id).hide();
    comm.send(data);

    // Register handler for displaying dataset rows.
    comm.on_msg(function(msg) {
        render_table(div_id, msg.content.data);
        render_commands(div_id, msg.content.data);
        // Hide loader and add command list.
        $('#loader').hide()
        $(div_id).show();
    });
}


/*
 * Render submit button for command forms.
 */
function render_button(div_id, ds, action) {
    const args = '\'' + div_id + '\', \'' + ds.name + '\', \'' + ds.engine + '\'';
    const html = '<button onclick="exec_command(' + args + ')" type="button" on>Submit</button>';
    $(div_id).append('<div style="margin-top: 1em;">' + html + '</style>');
}


/*
 * Fake render commands. Renders a dropdown with column names and a 'submit'
 * button for each registered function.
 */
function render_commands(div_id, data) {
    $(div_id).append('<h3>Update column using a registered command</h3>');
    // Create a drop-down with column names and two buttons for converting
    // column values to upper and lower case.
    let columns = '';
    for (let i = 0; i < data.columns.length; i++) {
        const col = data.columns[i];
        columns += '<option value="' + col.name + '">' + col.name + '</option>';
    }
    // Create a dropdown with available command names.
    let commands = '';
    for (let i = 0; i < data.commands.length; i++) {
        const cmd = data.commands[i];
        commands += '<option value="' + cmd + '">' + cmd + '</option>';
    }
    // Create the submit button.
    const ds = data.dataset;
    const args = '\'' + div_id + '\', \'' + ds.name + '\', \'' + ds.engine + '\'';
    const btn = '<button onclick="exec_command(' + args + ')" type="button" on>Submit</button>';
    // Combine components of the submit form.
    let html =  '<style> .form-line { margin: 1em; } .form-label { font-weight: bold; margin-right: 1em; }</style>';
    html += '<div class="form-line"><p class="form-label">Column</p><select id="colSelect">' + columns + '</select></div>';
    html += '<div class="form-line"><p class="form-label">Command</p><select id="cmdSelect">' + commands + '</select></div>';
    html += '<div class="form-line">' + btn + '</div>';
    $(div_id).append(html);
}


/*
 * Render table for dataset rows. The data object contains the dataset columns,
 * rows, and the dataset locator.
 */
function render_table(div_id, data) {
    // The data object contains the list of column names ('columns') and
    // a list of rows ({'id': row identifier, 'values': [cell values]})
    let header = '';
    for (let i = 0; i < data.columns.length; i++) {
        header += '<th>' + data.columns[i].name + '</th>';
    }
    header = '<thead>' + header + '</thead>';
    let body = '';
    for (let i = 0; i < data.rows.length; i++) {
        const values = data.rows[i].values;
        let row = '';
        for (let j = 0; j < values.length; j++) {
            row += '<td>' + values[j] + '</td>';
        }
        body += '<tr>' + row + '</tr>';
    }
    body = '<tbody>' + body + '</tbody>';
    let html = '<table style="width: 100%;">' + header + body + '</table>';
    $(div_id).html(html);
}
