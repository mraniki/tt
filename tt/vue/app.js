

import { createApp, ref } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'


const app = createApp({
		    setup() {
		      const message = ref('Hello U!')
		      return {
		        message
		      }
		    }
		  }).mount('#app')