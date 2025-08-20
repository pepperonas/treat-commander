module.exports = {
  apps: [{
    name: 'treat-commander',
    script: 'server.py',
    interpreter: 'python3',
    cwd: '/home/pi/apps/treat-commander',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PORT: 5007,
      FLASK_ENV: 'production',
      ARDUINO_PORT: '/dev/ttyACM1'
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 5007,
      FLASK_ENV: 'production',
      ARDUINO_PORT: '/dev/ttyACM1'
    },
    error_file: '/home/pi/apps/treat-commander/logs/error.log',
    out_file: '/home/pi/apps/treat-commander/logs/out.log',
    log_file: '/home/pi/apps/treat-commander/logs/combined.log',
    time: true,
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    kill_timeout: 5000,
    restart_delay: 2000,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};