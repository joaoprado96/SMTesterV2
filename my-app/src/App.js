import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const dropdownOptions = [
    {
      label: 'Monitor:',
      options: ['TESTER1', 'TESTM26', 'AGENRT3'],
    },
    {
      label: 'Port:',
      options: ['5033', '5034', '25000'],
    },
    {
      label: 'Conexões:',
      options: ['1','2','3','4','5','6','7','8','9','10','20','30','40','50','60','70','80','90','100'],
    },
    {
      label: 'Tipo de Terminal',
      options: ['11','71','20','90'],
    },
    {
      label: 'Nome da Conexão',
      options: ['SMTESTE0','SMTESTE1','SMTESTE2','SMTESTE3','SMTESTE4','SMTESTE5','SMTESTE6','SMTESTE7','SMTESTE8','SMTESTE9'],
    },
    {
      label: 'Número de Série',
      options: ['0xxxx', '1xxxx', '2xxxx', '3xxxx', '4xxxx', '5xxxx','6xxxx', '7xxxx', '8xxxx', '9xxxx'],
    },
    {
      label: 'Tipo de Protocolo',
      options: ['4000A', '2000A'],
    },
    {
      label: 'Serviço',
      options: ['PW10002X', 'VQ10001X', 'Opção 3 - Opção N'],
    },
    {
      label: 'Transação',
      options: ['CL1', 'OTS', 'OTT'],
    },
  ];

  const [dropdownValues, setDropdownValues] = useState(Array.from({ length: 15 }, () => ''));
  const [sliderValues, setSliderValues] = useState(Array.from({ length: 5 }, () => 0));
  const [textInput, setTextInput] = useState('');
  const [messages, setMessages] = useState([]);

  const handleDropdownChange = (index, value) => {
    setDropdownValues(prevValues => {
      const newValues = [...prevValues];
      newValues[index] = value;
      return newValues;
    });
  };

  const handleSliderChange = (index, value) => {
    setSliderValues(prevValues => {
      const newValues = [...prevValues];
      newValues[index] = value;
      return newValues;
    });
  };

  const handleTextInputChange = e => {
    setTextInput(e.target.value);
  };

  const handleSubmit = async e => {
    e.preventDefault();

    const jsonData = {
      dropdownValues,
      sliderValues,
      textInput
    };

    try {
      const response = await axios.post('http://localhost:8000', jsonData);
      const message = response.data.message;
      setMessages(prevMessages => [...prevMessages, message]);
    } catch (error) {
      console.error('Erro ao enviar os dados:', error);
    }

    setDropdownValues(Array.from({ length: 9 }, () => ''));
    setSliderValues(Array.from({ length: 5 }, () => 0));
    setTextInput('');
  };

  return (
    <div className="container">
      <div className="row">
        <div className="col-md-6">
          <h1>Service Master Tester</h1>
          <form onSubmit={handleSubmit}>
          <button type="submit">Enviar</button>
            {dropdownOptions.map((option, index) => (
              <div key={index}>
                <label htmlFor={`dropdown-${index}`}>{option.label}</label>
                <select
                  id={`dropdown-${index}`}
                  className="form-control"
                  value={dropdownValues[index]}
                  onChange={e => handleDropdownChange(index, e.target.value)}
                >
                  <option value="">Selecione...</option>
                  {option.options.map((subOption, subIndex) => (
                    <option key={subIndex} value={subOption}>
                      {subOption}
                    </option>
                  ))}
                </select>
              </div>
            ))}
           <div className="form-group">
            <label htmlFor="textInput">Entrada de Texto:</label>
            <input
              type="text"
              id="textInput"
              className="form-control"
              value={textInput}
              onChange={handleTextInputChange}
            />
           </div>
            <div>
              <h2>Barras deslizantes</h2>
              {Array.from({ length: 5 }, (_, i) => (
                <div key={i}>
                  <label htmlFor={`slider-${i}`}>Opção {i + 1}</label>
                  <input
                    type="range"
                    id={`slider-${i}`}
                    min="0"
                    max="100"
                    value={sliderValues[i]}
                    onChange={e => handleSliderChange(i, parseInt(e.target.value))}
                  />
                  <span>{sliderValues[i]}</span>
                </div>
              ))}
            </div>
          </form>
        </div>
        <div className="col-md-6">
          <h1>Mensagens do Backend</h1>
          <div className="message-box">
            {messages.map((message, index) => (
              <p key={index}>{message}</p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );  
}

export default App;