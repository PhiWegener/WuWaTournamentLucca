<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const bosses = ref([])
const form = ref({ id: null, name: '', hp: 0, element: '' })
const editing = ref(false)

async function load() {
  const res = await api.get('/bosses')
  bosses.value = res.data
}

function edit(boss: any) {
  form.value = { ...boss }
  editing.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/bosses/${form.value.id}`, form.value)
  } else {
    await api.post('/bosses', form.value)
  }
  form.value = { id: null, name: '', hp: 0, element: '' }
  editing.value = false
  load()
}

async function remove(id: number) {
  await api.delete(`/bosses/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div class="admin-content">
    <h1>Manage Bosses</h1>

    <form class="edit-form fx-glow">
      <input v-model="form.name" placeholder="Name" />
      <input v-model.number="form.hp" type="number" placeholder="HP" />
      <input v-model="form.element" placeholder="Element" />
      <button class="ww-btn" @click.prevent="save">{{ editing ? 'Update' : 'Create' }}</button>
    </form>

    <table class="table">
      <thead>
        <tr><th>Name</th><th>HP</th><th>Element</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="b in bosses" :key="b.id">
          <td>{{ b.name }}</td>
          <td>{{ b.hp }}</td>
          <td>{{ b.element }}</td>
          <td>
            <button @click="edit(b)">Edit</button>
            <button @click="remove(b.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

