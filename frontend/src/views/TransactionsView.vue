<template>
  <div class="blockbase">
    <div class="text-center">
      <button class="btn btn-light" v-on:click="showTable">Обновить</button>
    </div>
    <table class="table">
    <thead>
      <tr>
        <th scope="col">#</th>
        <th scope="col">parentBlockID</th>
        <th scope="col">msg</th>
        <th scope="col">data</th>
        <th scope="col">fee</th>
        <th scope="col">value</th>
        <th scope="col">fromAddr</th>
        <th scope="col">toAddr</th>
        <th scope="col">timestamp</th>
        <th scope="col">ttype</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="transaction in transactions" :key="transaction.id">
        <td class="text-break">{{transaction.id}}</td>
        <td class="text-break">{{transaction.parentBlockID}}</td>
        <td class="text-break">{{transaction.msg}}</td>
        <td class="text-break">{{transaction.data}}</td>
        <td class="text-break">{{transaction.fee}}</td>
        <td class="text-break">{{transaction.value}}</td>
        <td class="text-break">{{transaction.fromAddr}}</td>
        <td class="text-break">{{transaction.toAddr}}</td>
        <td class="text-break">{{transaction.timestamp}}</td>
        <td class="text-break">{{transaction.ttype}}</td>
      </tr>
    </tbody>
  </table>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data: () => ({ transactions: [] }),
  methods: {
    showTable(){
      axios
          .get('/transaction')
          .then(response => {
            this.transactions = response.data
          })
          .catch(function (error) {
            console.log(error);
          })
    }
  }
}

</script>