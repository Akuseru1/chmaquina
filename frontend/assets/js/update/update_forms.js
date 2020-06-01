import {getData, getRunAll, getPaso} from '../retrieving/data.js';

// let memory_table = document.getElementById('memory')

let variables_table = document.getElementById('var');
let tags_table = document.getElementById('tag');
let instruction_table = document.getElementById('instruction')
let registers_table = document.getElementById('registers')

let variables    = [];
let tags         = [];
let programs     = [];
let originals    = [];
let colors = ["#212121", "#330077",'#7a1b6c', '#303030', "blue", "green"];

getData()
.then(data => {
    consoleLogData(data);

    data['variables'].forEach(element => variables.push(element));
    createTable(variables_table, variables);

    data['tags'].forEach(element => tags.push(element) );
    createTable(tags_table, tags);

    data['programs'].forEach(program => programs.push(program));
    createTableInstructions(instruction_table, programs);

    if(data['programs'].length >= 1)
        createTableRegisters(registers_table, data['registers'])
})
.then(() => {
    const correrButton = document.getElementById("correr")
    correrButton.addEventListener("click", e => {
        getRunAll()
        .then(data => {
            console.log("after_run: ", data['stdout'])
            console.log("steps: ", data['steps'])
            let monitor = document.getElementById('monitor')
            data['stdout'].forEach(element => {
                monitor.innerHTML += element+"\ ";
            });
        });
    });

    const limpiarButton = document.getElementById("limpiar")
    limpiarButton.addEventListener("click", e => {
        e.preventDefault();
        const endpoint  = 'http://localhost:8000/api/clean';
        variables_table.innerHTML   = originals[0];
        tags_table.innerHTML        = originals[1];
        instruction_table.innerHTML = originals[2];
        registers_table.innerHTML   = originals[3];
        const memoria = document.getElementById("memoria");
        const kernel = document.getElementById("kernel");
        const acumulador = document.getElementById("acumulador");
        let data = {'memoria': memoria.value, 'kernel': kernel.value, 'acumulador': acumulador.value};
        fetch(endpoint, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        }).catch(console.error);

    });
});

function consoleLogData(data) {

    console.log("All: "             , data);
    console.log("acumulador: "      , data['acumulador']);
    console.log("variables: "       , data['variables']);
    console.log("tags: "            , data['tags']);
    console.log("programs: "        , data['programs']);
    console.log("registers: "       , data["registers"])
    console.log("memory Available: ", data["memoryAvailable"])
    console.log("memory used: "     , data["memoryUsed"])
}

function createLeaForm(leaItems) { // pasa la liista, cuando presione el boton ok, continuar con next
    let numLea = leaItems.length;
    let lea = document.getElementById('lea');
    let leaButton = document.getElementById('leaButton');
    if(numLea == 0) {
        lea.setAttribute('style', "display: none");
        leaButton.setAttribute('style', "display: none");
        return;
    }
    lea.setAttribute('style', "display: block");
    leaButton.setAttribute('style', "display: block");
    lea.setAttribute('placeholder', "ingrese un valor para " + leaItems[0]);
    leaButton.addEventListener("click", function press() {
        let data = {'lea': lea.value};
        const endpoint  = 'http://localhost:8000/api/lea';
        fetch(endpoint, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
        .then(() => {
            lea.value = "";
            leaItems.shift();
            leaButton.removeEventListener("click", press);
            createLeaForm(leaItems);
        })
        .catch(console.error);
    });
}

function createTable(table, listElements) {
    let id = 0;
    let current_color = 0;
    originals.push(table.innerHTML); //for the clean button
    listElements.forEach(program => {
        program.forEach(element => {
            table.innerHTML += '<tbody style="background-color:'+ colors[current_color] + '" >\ <tr> \ <td>' + id++ + '</td> \ <td>' + element + '</td> \ </tr>\ </tbody>';
        });
        current_color++;
    });
}

function createTableInstructions(table, listInstructions) {

    let id = 0;
    let current_color = 0;
    let leaItems = []
    let numInstructions = listInstructions.length
    let current_instruction = 0;
    originals.push(table.innerHTML); // for the clean button
    
    listInstructions.forEach(instruction =>{
        current_instruction++;
        instruction.forEach(element => {
            
            if(current_instruction == numInstructions) { // if last instruction check lea
                if(element[0] == "lea") {
                    leaItems.push(element[1]);
                }
            }
            element = element.join(' ')
            table.innerHTML += '<tbody style="background-color:'+ colors[current_color] + '" >\ <tr> \ <td>' + id++ + '</td> \ <td>' + element + '</td> \ </tr>\ </tbody>';
        });
        current_color++;
    });

    createLeaForm(leaItems);       
}
let idProg = 1;
function createTableRegisters(table, registers) {
    let filenames       = registers[0];
    let instruction_num = registers[1];
    let rb              = registers[2];
    let rlc             = registers[3];
    let rlp             = registers[4];
    let length = rb.length;
    originals.push(table.innerHTML);
    for(let i=0; i< length; i++) {
            table.innerHTML += '<tbody style="background-color:'+colors[i]+ '" >\ <tr> \ <td> 000' + idProg++ + '</td> \ <td>' + filenames[i] + '</td> \ <td>' + instruction_num[i] + '</td> \ <td>' + rb[i] + '</td> \  <td>' + rlc[i] + '</td> \ <td>' + rlp[i] + '</td> \ </tr>\ </tbody>';
    }
}
