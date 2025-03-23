function Heater(props) {
  const styles = {
    container: {
      textAlign: 'center',
      padding: '20px',
      maxWidth: '300px',
      margin: '0 auto',
      border: '1px solid #ccc',
      borderRadius: '10px',
      backgroundColor: '#f9f9f9',
    },
    tempDisplay: {
      marginBottom: '20px',
    },
    buttonContainer: {
      marginBottom: '20px',
    },
    button: {
      fontSize: '18px',
      padding: '10px 20px',
      margin: '0 10px',
      backgroundColor: '#007BFF',
      color: 'white',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
    },
    lightControl: {
      marginTop: '20px',
    },
  };

  return (
    <div>
      <h1>{props.name}</h1>
      <div style={styles.tempDisplay}>
        <div>
          <h2>Set Temperature: {props.setTemp}°C</h2>
          <h3>Current Temperature: {props.currentTemp}°C</h3>
        </div>
      </div>

      <div style={styles.buttonContainer}>
        <button onClick={props.increaseTemp} style={styles.button}>↑</button>
        <button onClick={props.decreaseTemp} style={styles.button}>↓</button>
      </div>

      <div style={styles.lightControl}>
        <button onClick={props.toggleLight} style={styles.button}>
          {isLightOn ? 'Turn Off Light' : 'Turn On Light'}
        </button>
        <p>Light is {props.isLightOn ? 'ON' : 'OFF'}</p>
      </div>
    </div>
  )



}

export default Heater
