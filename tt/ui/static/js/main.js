// import { createApp }  from 'https://unpkg.com/vue@3/dist/vue.global.prod.js'
import { createApp } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js'
import App from './App.vue'


const app = createApp(App)
app.config.compilerOptions.delimiters = ['[[', ']]']
app.mount("#app")

		<script src="{{ url_for('static', filename='js/main.js') }}" ></script>