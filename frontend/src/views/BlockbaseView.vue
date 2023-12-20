<template>
  <div class="blockbase">
    <div class="text-center">
      <button class="btn btn-light" v-on:click="showTable">Обновить</button>
    </div>
    <table class="table">
    <thead>
      <tr>
        <th scope="col">#</th>
        <th scope="col">prevHash</th>
        <th scope="col">nonce</th>
        <th scope="col">datastring</th>
        <th scope="col">hash</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="block in blocks" :key="block.id">
        <td class="text-break">{{block.id}}</td>
        <td class="text-break">{{block.prevHash}}</td>
        <td class="text-break">{{block.nonce}}</td>
        <td class="text-break">{{block.datastring}}</td>
        <td class="text-break">{{block.hash}}</td>
      </tr>
    </tbody>
  </table>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data: () => ({ blocks: [] }),
  methods: {
    showTable(){
      axios
          .get('/block')
          .then(response => {
            this.blocks = response.data
          })
          .catch(function (error) {
            console.log(error);
          })
    }
  }
}

</script>