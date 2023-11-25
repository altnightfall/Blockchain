<template>
  <div class="home">
    <img alt="Bitkoin logo" src="../assets/logo.png">
    <HelloWorld/>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue';

export default {
  name: 'HomeView',
  components: {
    HelloWorld,
  },
}
</script>
