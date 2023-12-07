<template>
  <div class="home">
    <div class="text-center">
      <button class="btn btn-light" v-on:click="showTable">Обновить</button>
    </div>
    <table class="table">
    <thead>
      <tr>
        <th scope="col">#</th>
        <th scope="col">First</th>
        <th scope="col">Last</th>
        <th scope="col">Handle</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="user in users" :key="user.email">
        <td>{{user.name}}</td>
        <td>{{user.username}}</td>
        <td>{{user.email}}</td>
        <td>{{user.phone}}</td>
      </tr>
    </tbody>
  </table>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data: () => ({ users: [] }),
/*  mounted() {
    axios
        .get('https://jsonplaceholder.typicode.com/users')
        .then(response => {
          this.users = response.data
        })
        .catch(function (error) {
          console.log(error);
        })
  },*/
  methods: {
    showTable(){
      axios
          .get('https://jsonplaceholder.typicode.com/users')
          .then(response => {
            this.users = response.data
          })
          .catch(function (error) {
            console.log(error);
          })
    }
  }
}

</script>